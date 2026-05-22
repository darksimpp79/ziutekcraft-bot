from mcrcon import MCRcon

with MCRcon('localhost', 'zaq1@WSX', port=25575) as r:
    print(r.command('whitelist list'))
    print(r.command('whitelist add dragon2'))
    print(r.command('whitelist list'))
