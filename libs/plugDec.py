import rsa, base64

def dec_plug(bskey, plugbyt):
    priks = [
        "809d340859f1a84e885b763eec850eab16f0efdcf4ad0bbc7ba368a2e1cbb36dc918f41802c244914bfc97ff12f9e9529291f03367a5bfce07140972c9f5c2ad",
        "10001",
        "22f699668bccfe0c1b5581d7a944a2b030145fa09983516573d70063072eac8be5830ac97fd0fecfd7ef74195a8234991e6e23258a9fadc787bc6bad4101a1a1",
        "fc45a32d2181b4eb7d51a4f1e03a48469bcb545c7c6b831b4447bf25de69012200c7",
        "8283c25d85d4131b8ed57adf3a488cd8e47f28dce5de069492207a5494eb"
    ]
    prik = rsa.PrivateKey(*[eval("0x"+u) for u in priks])
    k = rsa.decrypt(bskey, prik).decode('utf-8')
    fplug = __dec(plugbyt, k)
    return compile(fplug)

def __dec(s: bytes, k):
    o_str = base64.b85decode(s.decode('ascii')).decode()
    dec_str = ""
    for i, j in zip(o_str, k):
        temp = chr(ord(i) - ord(j))
        dec_str = dec_str + temp
    return dec_str