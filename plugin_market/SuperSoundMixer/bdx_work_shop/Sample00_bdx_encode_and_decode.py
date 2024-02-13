import os
import json

from canvas import BdxEncoder
from canvas import BdxDecoder

# 根据官网 bdump 格式，https://github.com/LNSSPsd/PhoenixBuilder/blob/main/BDump%20File%20Format.md
# decoder 将 bdx 文件解码为 操作列表,作者,缓存/调色板中方块 的字典
# decoder 输出格式为 op_code, op_name, params
# encoder 将操作列表编码为bdx 但是支持较为宽松的格式 (见示列)
# decoder 和 encoder 都支持验证签名/添加签名
# decoder 和 encoder 都支持生成易于人类阅读的日志文件，并可以配置输出哪些操作的信息，在一些情况下，知道究竟发生了什么可能很有帮助
# 将 decoder 的输出作为encoder的输入时，保证可以生成和fb源文件一样的压缩文件(本文件)
# 缺陷是，decoder和encoder都偏底层，没有提供官网之外的高级操作的api，这部分需要自己实现

decoder_input_bdx='data/silo.bdx'
decoder_output_cmds='output/sample00/decoder_out_cmds.json'
decoder_output_logs='output/sample00/decoder_out_logs.txt'

encoder_output_logs='output/sample00/encoder_out_logs.txt'
encoder_output_bdx='output/sample00/encoder_out_bdx.bdx'

os.makedirs('output/sample00',exist_ok=True)

# 配置bdx解析器 配置日志输出位置，为None时输出到屏幕 配置是否验证签名
decoder = BdxDecoder(decoder_output_logs, need_verify=True)
# 过滤日志输出内容
# decoder.log_nothing()
decoder.log_command_block_only()
# decoder.log_everthing()
# decoder.log_level.update({'place_block':0})

# 打开目标bdx，并解码
print('decoding...')
with open(decoder_input_bdx, 'rb') as f:
    # 解码后生成为操作列表(list)，作者，缓存/调色板中方块，最终位置构成的字典
    # 每项操作的格式为 op_code, op_name, params
    # 其中，op 没有参数时 params 为 None
    # op 参数一个时 params 为参数(i.e., block_data:int)
    # op 参数超过一个时 params 为tuple
    decode_out = decoder.decode(f)
    print('decoding done, write file...')
    with open(decoder_output_cmds, 'w') as f:
        json.dump(decode_out, f)
        print('decoded cmds dumped!')

# 配置bdx编码器 配置日志输出位置，为None时输出到屏幕 配置是否验证签名
# 签名所需fbtoken 默认为 fb 存放token的位置，也可以将字符串或者路径传入
encoder = BdxEncoder(need_sign=True, log_path=encoder_output_logs, author='2401PT',sign_token=None)
# 过滤日志输出内容，和上面一样
# encoder.log_nothing()
encoder.log_command_block_only()
# encoder.log_everthing()


print('encoding...')
# 将操作列表(cmds list)编码为bdx
# 每项操作格式可以为 op_code, op_name, params； 也可以为 op_code, params； 也可以为 op_name, params;
# op 中 params 可以为列表也可以为字典；
# op 中 block可以为调色板中的序号也可以为方块名
# author,palette 是可选的,
# sign_token为None时默认查找fb自动生成的token
# encode_out 就是生成的bdx文件二进制信息，直接wb写到文件中即可
encoded_out_bytes = encoder.encode(cmds=decode_out["cmds"],
                            author=decode_out["author"],
                            palette=None, # decode_out['palette'], 该参数是可选的，仅在命令中包含也可
                            sign_token=None)
print('encoding done, write file...')
with open(encoder_output_bdx, 'wb') as f:
    f.write(encoded_out_bytes)
    print('encoded bdx saved!')


def compare_bytes_array(array_1,array_2):
    ok = True
    if len(array_1) != len(array_2):
        print(f'length_mismathced {len(array_1)} {len(array_2)}')
        ok = False
    for i, (e, d) in enumerate(zip(array_1, array_2)):
        if e != d:
            print(f'error occur at {i}')
            print(f'{array_1[max(0, i - 20):min(len(array_2), i + 10)]}')
            print(f'{array_1[max(0, i - 20):min(len(array_2), i + 10)]}')
            ok = False
            break
    print('pass' if ok else 'fail')


# encode_bdx_bytes 为bdx文件（未压缩）从 BDX\x00 之后到文件最后
encode_bdx_bytes = encoder.bdx_bytes
# decode_bdx_bytes 为bdx文件（解压缩）从 BDX\x00 之后到文件最后
decode_bdx_bytes = decoder.bdx_bytes

print('check if the binary code of uncompressed cmds by encoder/decoder is correct')
compare_bytes_array(encode_bdx_bytes,decode_bdx_bytes)

print('check if the binary code of bdx file outputted by decoder is correct')
with open(decoder_input_bdx, 'rb') as f:
    original_bdx_bytes = f.read()
compare_bytes_array(original_bdx_bytes,encoded_out_bytes)

print('all done')