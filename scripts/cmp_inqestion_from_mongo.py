#!/usr/bin/env airpython
# -*- coding: utf-8 -*-
"""
Author: Veaceslav Kunitki<tumikosha@gmail.com>
Description: pipleine for ingesting data into company table
"""

import datetime
import os
from typing import Tuple
import pymongo as pymongo

import tumi_summary
from scripts.constants import MONGO_URI, proxy_nest, DENIED, dummy_list
from tumi_tools.mongo_cache import mongo_cache
from tumi_tools.tumi_selenium import get_page_via_selenium
from tumi_tools.tumi_speed import measure_execution_time
from util.calendly_cached import get_events_by_nicks
from util.common import string_2_uuid, html_2_txt_tit_fav, first_item_or_none, prepare_img_path, to_date_none, \
    to_int_none, clear_phones
import argparse
import logging

# logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(encoding='utf-8', level=logging.ERROR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "general.settings")
# import django
# django.setup()
from app import setup
import pandas as pd

setup()

from app.models import Company
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("all-MiniLM-L6-v2")


def load_csv(path) -> pd.DataFrame:
    """ load csv to df """
    with measure_execution_time("loading dataset"):
        mydf = pd.read_csv(path, index_col=False, on_bad_lines='skip', delimiter=",")
    with measure_execution_time("indexing dataset"):
        mydf.set_index('Root_Domain', inplace=True)  # Setting 'Name' as the index

    return mydf


@mongo_cache(MONGO_URI, db_name="fixiegen", collection="sites_with_cal_cache",
             ttl=datetime.timedelta(days=60), verbose=True)
def load_url(url):
    res = proxy_nest.get(url)
    return res.status_code, res.text


@mongo_cache(MONGO_URI, db_name="fixiegen", collection="sites_cal_cache_selen",
             ttl=datetime.timedelta(days=60), verbose=True)
def load_url_selenium(url: str) -> Tuple[int, str]:
    try:
        response = get_page_via_selenium(url, sleep=2, proxy=None)
        return response.status_code, response.text
    except Exception as e:
        return 408, None


def remove_substr(field, sub: str):
    return field if not isinstance(field, str) else field.replace(sub, "")


def process_calendly_links(links: dict):
    return links


def transfer_mongo_cal_links_2_pg(df, offset=0, limit=100, min_text_cut=10):
    client = pymongo.MongoClient(MONGO_URI)
    db = client["fixiegen"]
    # q = {"$and": [{"status": "Ok"}, {"txt": {"$exists": True}}]}
    q = {"$and": [{"status": "Ok"}]}
    total = db.cal_sites.count_documents(q)
    print("Total", total)
    cursor = db.cal_sites.find(q, no_cursor_timeout=True).skip(offset).limit(limit)
    counter, txt_counter = 0, 0
    for idx, row in enumerate(cursor):
        print(row['_id'])
        status, html = load_url_selenium(f"https://{row['_id']}")
        # status, html = load_url(f"https://{row['_id']}")
        if (html is None) or (status != 200): continue
        # html = row['html']
        # html = row['html']
        if any(map(html.__contains__, DENIED)):  # skip bad pages
            continue
        if row.get("cal_links", None) is None:  # skip pages without calendly links
            continue
        text, title, fav, desc, h1, h2 = html_2_txt_tit_fav(html)
        print(f"{row['_id']}, {len(text)}, {fav},\n {title} \n {desc} \n h1: {h1}\n h2: {h2}")
        # text = row['txt']
        # here we start transform
        counter = counter + 1
        if len(text) > min_text_cut: txt_counter = txt_counter + 1
        if len(text) <= min_text_cut: continue
        if row["links_num"] < 1: continue  # if only one link on page

        df_row = df.loc[row['_id']]

        # only if calendly.com link on first page
        if df_row['Location_on_Site'] != row["_id"]: continue

        calendly_lst = get_events_by_nicks(row["cal_links"], headless=True)
        # calendly = {"ver": 1, "links": row["cal_links"]}
        calendly = calendly_lst  # save list as JSON !
        print("Calendly:", row["cal_links"])
        print("CALENDLY:", calendly)
        # calculating list of events
        calendly_acc_num, calendly_events_num, open_days_num = 0, 0, 0
        for cal in calendly_lst:
            calendly_events_num += len(cal['events'])
            for event in cal['events']:
                open_days_num += event.get("dates_num", 0)
        summary = tumi_summary.summarize(text, tumi_summary.SumBasicSummarizer)
        name = df_row["Company"] if isinstance(df_row["Company"], str) else None
        domain = row["_id"]
        txt_4_vector = str(text) + " " + str(name) + str(row["_id"]) \
                       + str(title) + " " + str(df_row["Vertical"]) \
                       + str(calendly) + \
                       first_item_or_none(desc, default="")
        vector = encoder.encode(txt_4_vector).tolist()  # !!!!!!!!!!!!!!!!

        defaults = {
            "domain": domain,  # doc['domain'],
            "name": name,
            "title": title,
            "phones": clear_phones(df_row["Telephones"]),
            "emails": df_row["Emails"],
            "emails_json": df_row["Emails"].split(";") if isinstance(df_row["Emails"], str) else None,
            "phones_json": df_row["Telephones"].split(";") if isinstance(df_row["Telephones"], str) else None,
            # "description": summary,
            "description": first_item_or_none(desc),
            "summary": summary,
            "full_txt": text,
            "industry": df_row["Vertical"],

            "sales_revenue": df_row["Sales_Revenue"],
            "revenue": df_row["Revenue"],
            "employees": to_int_none(df_row["Employees"]),
            "first_indexed": to_date_none(df_row["First_Indexed"]),

            "logo": prepare_img_path(domain, first_item_or_none(fav)),
            "linkedin": remove_substr(df_row["LinkedIn"], "linkedin.com"),
            "youtube": remove_substr(df_row["YouTube"], "youtube.com"),
            "vimeo": remove_substr(df_row["Vimeo"], "vimeo.com"),
            "vk": remove_substr(df_row["Vk"], "vk.com"),
            "facebook": remove_substr(df_row["Facebook"], "facebook.com"),
            "twitter": remove_substr(df_row["Twitter"], "twitter.com"),
            "instagram": remove_substr(df_row["Instagram"], "instagram.com"),
            "google": df_row["Google"],
            "threads": df_row["Threads"],
            "github": df_row["GitHub"],
            "calendly": calendly,
            "calendly_acc_num": len(calendly)if calendly is not None else 0,  # len(row["cal_links"]),
            "calendly_events_num": calendly_events_num,  # len(row["cal_links"]),
            "calendly_open_days_num": open_days_num,  # len(row["cal_links"]),
            # "zip": df_row["Zip"],
            # "city": df_row["City"],
            # "country": df_row["Country"],
            # "state": df_row["State"],

            "embedding": vector,
        }
        copy = dict(defaults)
        del copy['embedding']
        del copy['description']
        del copy['summary']
        del copy['full_txt']
        txt_flag = "!" if len(text) < 10 else ""
        print(idx, txt_flag, row["_id"], counter, txt_counter, copy)
        company, created = Company.objects.update_or_create(
            id=string_2_uuid(row["_id"]), defaults=defaults)

        row['summary'] = tumi_summary.summarize(text, tumi_summary.SumBasicSummarizer)
        # row['summary_lsa'] = tumi_summary.summarize_lsa(text)
        # row['summary_lex_rank'] = tumi_summary.summarize_lex_rank(text)
        # row['summary_luhn'] = tumi_summary.summarize_luhn(text)
        # row['summary_kl'] = tumi_summary.summarize_kl(text)

        # for doc in dummy_list:
        #     vector = encoder.encode(doc['summary']).tolist()
        #     company, created = Company.objects.update_or_create(
        #         id=string_2_uuid(doc['domain']),
        #         defaults={
        #             "title": doc['title'],
        #             "domain": doc['domain'],
        #             "summary": doc['summary'],
        #             "embedding": vector
        #         }
        #     )
        #     company.save()


def main():
    """
    The main function that executes the script.
    """
    # Your code here
    parser = argparse.ArgumentParser(description='A simple script with command-line arguments.')
    parser.add_argument('--limit', '-l', help='limit', type=int, default=10000)
    parser.add_argument('--offset', '-o', help='offset', type=int, default=1)
    # parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose mode')
    args = parser.parse_args()

    df = load_csv("/media/tumi/prj/_DATASETS/calendly.com/web-sites-with-calendly-link.csv")
    print("Companies count in DB:", Company.objects.count())
    with measure_execution_time("loading dataset"):
        transfer_mongo_cal_links_2_pg(df, offset=args.offset, limit=args.limit, min_text_cut=50)
    print("Companies count in DB:", Company.objects.count())
    print("Done...")


if __name__ == "__main__":
    main()

# 37 Mb container started on empty folder
# 46 Mb after creating  "Vector_db"
# 46 Mb after migrate.sh  "Vector_db"
# 73 Mb for  1k records
# 214 Mb for  10k records
# 324 Mb for  17661 records

# 54 Mb after deleting Vector_db
