def encode(string):
    encoder = {" ":"🪐","a":"🍎","b":"📚","c":"🐈","d":"🐬","e":"🌍","f":"🐟",
               "g":"🐐","h":"🐴","i":"🧊","j":"🛩","k":"🔑","l":"🪵",
               "m":"⛰","n":"🥜","o":"🐙","p":"🏓","q":"👸",
               "r":"🌧","s":"☀","t":"🌳","u":"☂","v":"🏖","w":"🥇","x":"❌",
               "y":"✌","z":"🦓"}
    code = [encoder[c] for c in string]
    print("".join(code))

i = input()
while(i!="-"):
    encode(i)
    i = input()