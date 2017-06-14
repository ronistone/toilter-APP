from flask import g,jsonify,request
from flask_restful import Resource, reqparse
from app import app, db, auth, api
from app.models.tables import User, Follow, Post
from itertools import chain
from sqlalchemy import func

@auth.verify_password
def verify_password(email_or_name,password):
    if email_or_name is not None:
        user = User.verify_auth_token(email_or_name)
        if not user:
            user = User.query.filter_by(email=email_or_name).first()
            if not user:
                user = User.query.filter(func.lower(User.name)==func.lower(email_or_name)).first()
            if not user or not user.verify_password(password):
                return False

            g.user = user
            return True
        g.user = user
        return True
    return False

@app.route('/api/v1/tokens', methods=['GET'])
@auth.login_required
def get_auth_token():
    """
        This function returns a token for authentication.
        It guarantees the security of user's information.
    """
    token = g.user.generate_auth_token()
    token = token.decode('ascii')
    user = g.user
    user.token = token
    # print({'user': user.serialize})
    #return {'user': user.serialize, 'token': token},200
    response = jsonify({'user': user.serialize, 'token': token})
    response.status_code = 200
    return response


class UsersAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("name", type=str, required=True,
                                    location='json')
        self.reqparse.add_argument("email", type=str, required=True,
                                    location='json')
        self.reqparse.add_argument("password", type=str, required=True,
                                    location='json')
        super(UsersAPI,self).__init__()

    @auth.login_required
    def get(self):
        args = {}
        args['name'] = request.args.get('name')
        user = User.query.filter(User.name.ilike("%{0}%".format(args['name'])))
        return {'data': [u.serialize for u in user]},200

    def post(self):
        args = self.reqparse.parse_args()
        user = User(**args)

        user.hash_password(args['password'])
        db.session.add(user)

        try:
            db.session.commit()
            return {'data': user.serialize}, 200

        except Exception as error:
            print(error)
            return {'message':'ERROR'}, 500
class ModifyUserAPI(Resource):
    @auth.login_required
    def get(self,id):
        user = User.query.get_or_404(id)
        return {'data': user.serialize},200

class FollowAPI(Resource):

    @auth.login_required
    def get(self,id):
        args = {}
        args['follower'] = request.args.get('follower')
        try:
            if args['follower']:
                users = Follow.query.filter_by(user_id=id,follower_id=g.user.id).first()
                if users:
                    return {'data': True}, 200
                else:
                    return {'data': False},404
            else:
                users = Follow.query.filter_by(user_id=id).all()
                return {'data': [u.serialize for u in users]}, 200
        except Exception as error:
            print(error)
            return {'msg': 'ERROR'},500

    @auth.login_required
    def post(self,id):
        follow = Follow.query.filter_by(user_id=id,follower_id=g.user.id).first()
        if follow:
            return {'message':'Voce ja segue este usuario'}, 503
        else:
            follow = Follow(user_id=id,follower_id=g.user.id)
            db.session.add(follow)
            try:
                db.session.commit()
                return {"data":follow.serialize},200
            except Exception as error:
                print(error)
                return {'message':'ERROR'},500

    @auth.login_required
    def delete(self,id):
        follow = Follow.query.filter_by(user_id=id,follower_id=g.user.id).first()
        if follow:
            db.session.delete(follow)
            try:
                db.session.commit()
                return {'msg':'OK'},200
            except Exception as error:
                print(error)
                return {'msg':'ERROR'}, 500
        else:
            return {'msg':'voce nao segue este usuario'}, 503

class PostAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("content",type=str, required=True,
                                    location='json')
        super(PostAPI,self).__init__()
    @auth.login_required
    def get(self):
        post = Post.query.filter_by(user_id=g.user.id).limit(10).all()
        return {'data':[p.serialize for p in post]},200

    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        post = Post(**args)
        post.user_id = g.user.id

        db.session.add(post)

        try:
            db.session.commit()
            return {'data': post.serialize},200
        except Exception as error:
            print(error)
            return {'msg':'ERROR'},500
class ModifyPostAPI(Resource):
    @auth.login_required
    def get(self,id):
        posts = Post.query.filter_by(user_id=id).all()
        return {'data': [u.serialize for u in posts]},200

class DashboardAPI(Resource):

    @auth.login_required
    def get(self):
        args = {}
        try:
            args['num'] = int(request.args.get('num'))
            args['update'] = request.args.get('update')
            followers = Follow.query.filter_by(follower_id=g.user.id).all()
            posts = [Post.query.filter_by(user_id=u.user_id).all() for u in followers]
            posts += [Post.query.filter_by(user_id=g.user.id).all()]
            posts = list(chain(*posts))
            if args['update'] == "true":
                posts = posts[0:min(args['num'],len(posts))]
            else:
                args['init'] = int(request.args.get('init'))
                posts = posts[min(0,args['init']):min(len(posts),args['num']+args['init'])]
            posts = sorted(posts,key=lambda P: (P.h_post,P.id))
            print(posts)
            return {'data':[p.serialize for p in posts]},200
        except Exception as error:
            print(error)
            return {'msg':'Bad Request'},500


api.add_resource(UsersAPI, '/api/v1/users',endpoint='users')
api.add_resource(FollowAPI,'/api/v1/follow/<int:id>', endpoint='follow')
api.add_resource(PostAPI,'/api/v1/post',endpoint='post')
api.add_resource(DashboardAPI,'/api/v1/dashboard', endpoint='dashboard')
api.add_resource(ModifyUserAPI,'/api/v1/users/<int:id>', endpoint='modifyusers')
api.add_resource(ModifyPostAPI,'/api/v1/post/<int:id>', endpoint='modifyposts')
