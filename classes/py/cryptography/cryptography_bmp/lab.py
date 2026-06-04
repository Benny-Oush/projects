# import bmp
# # הצפנה 
# key = bmp.random_bmp(64, 64)
# spiral = bmp.load_bmp('cryptography_bmp/spiral.bmp')
# cipher = bmp.mod2(spiral, key)
# bmp.save_bmp(key, 'key.bmp')
# bmp.save_bmp(cipher, 'cipher.bmp')

# # פענוח

# key = bmp.load_bmp('key.bmp')
# cipher = bmp.load_bmp('cipher.bmp')
# msg = bmp.mod2(cipher, key)
# bmp.save_bmp(msg, 'msg.bmp')