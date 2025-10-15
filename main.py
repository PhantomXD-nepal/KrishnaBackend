from server import Server

if __name__ == '__main__':
    from gevent import monkey;
    monkey.patch_all()

    Server().run()
