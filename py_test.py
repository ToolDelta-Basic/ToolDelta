import re

s = re.compile("\[CQ:image,(.)*\]")

print(re.sub(s, "[图片]", "[CQ:image,file=75589e4fd9a10958067fe14eb4741109.image,subType=0]"))