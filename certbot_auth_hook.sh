#!/bin/bash
v="$CERTBOT_VALIDATION"
echo "$v" > /tmp/certbot_dns_value.txt
chmod 644 /tmp/certbot_dns_value.txt
echo "=== DNS TXT RECORD NEEDED ==="
echo "Value: $v"
echo "=============================="
while [ ! -f /tmp/certbot_dns_done.txt ]; do sleep 2; done
rm -f /tmp/certbot_dns_done.txt
exit 0
