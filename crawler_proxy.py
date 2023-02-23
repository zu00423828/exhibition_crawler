import http
import requests
import re
res = requests.get("https://www.sslproxies.org/")
proxy_ips = re.findall("\d+\.\d+.\d+.\d+:\d+", res.text)
print(proxy_ips)
print(len(proxy_ips))

vaild_ips = []
for ip in proxy_ips:
    try:
        res = requests.get("https://10times.com",
                           proxies={'http': ip, 'https': ip}, timeout=5)
        print(ip, res.status_code)
        vaild_ips.append(ip)
    except:
        # print(ip, "invalid")
        pass
with open('proxy_list.txt', 'w') as f:
    for ip in vaild_ips:
        f.write(ip+"\n")
