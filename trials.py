import my_funcs as mf
import re
html = "<p>294 Dancing in the Palm of His Hand <br /> Xu Qing walked into the house.</p>"
if re.search(r"<br />", html):
    print(html.split("<br />")[0] + "</p>" + "<p>" + html.split("<br />")[1])