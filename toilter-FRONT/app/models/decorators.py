from flask import g, abort
# python decorators are functions defined above other functions
# it will receive another function and do something with it


# this decorators verify if the user id in the arguments is the same
# as the logged in user
# if it is, it calls the original function, else the user is unauthorized

def is_user(func):
    def func_wrapper():
        if g.user is not None:
            abort(401)
        else:
            return func()
    return func_wrapper
