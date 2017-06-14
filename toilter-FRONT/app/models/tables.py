class User(object):
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return (self.id,self.token)

    def __init__(self,id,name,email):
        self.id = id
        self.name = name
        self.email = email

class Post(object):
        def __init__(self,content,user_id,h_post,id):
            self.content = content
            self.name = user_id
            self.h_post = h_post
            self.id = id
