# ---===users===----
curl -u admin:pass123456 -X 'GET' \
  'http://127.0.0.1:8877/api/Snippet/' \
  -H 'accept: application/json' \
  -H 'X-CSRFToken: cjTMHUIdrcXiC9dv1CE79zW3Zaa6yAdCDB4AOpiophZ1qofozvfjEdacHM5stPrm'

# ---==== snippets ===-----
curl -u admin:pass123456 -X 'POST' \
  'http://127.0.0.1:8877/api/Snippet/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: cjTMHUIdrcXiC9dv1CE79zW3Zaa6yAdCDB4AOpiophZ1qofozvfjEdacHM5stPrm' \
  -d '{
  "code": "2+2"
}'

echo "======="
echo ""

python manage.py test -v 2
