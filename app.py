import facebook
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from flask_bootstrap import Bootstrap
from flask.json import jsonify
import os

app = Flask(__name__)
app.secret_key = "my seceret key"
bootstrap = Bootstrap(app)


client_id = '675085149505409'
client_secret = '49ff0f110f6fc743cd5c53778a4983f5'
authorization_base_url = 'https://www.facebook.com/dialog/oauth'
token_url = 'https://graph.facebook.com/oauth/access_token'
redirect_uri ='https://manage-fb-page.herokuapp.com/facebook/callback'

refresh_url = token_url

@app.route("/")
def index():
    return render_template('home.html')


@app.route("/facebook")
def demo():
    """Step 1: User Authorization.
    Redirect the user/resource owner to the OAuth provider (i.e. Facebook)
    using an URL with a few key OAuth parameters.
    """
    facebook = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['manage_pages', 'publish_pages', 'email'])
    # facebook = facebook_compliance_fix(facebook)
    authorization_url, state = facebook.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    # print(session, authorization_url)
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.
@app.route("/facebook/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    

    facebook = OAuth2Session(client_id, redirect_uri=redirect_uri)

    token = facebook.fetch_token(token_url, client_secret=client_secret,authorization_response=request.url)
                               

    # We use the session as a simple DB for this example.
    session['oauth_token'] = token
    print(session)

    return redirect(url_for('.menu'))
 
 
@app.route("/menu", methods=["GET"])
def menu():
    return render_template('index.html')



@app.route("/profile", methods=["GET","POST"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    acebook = OAuth2Session(client_id, token=session['oauth_token'])
    access_token = session['oauth_token']['access_token']
    get_dict_userid = acebook.get('https://graph.facebook.com/me?').json()
    get_id=get_dict_userid['id']
    
    get_dict_pageid = acebook.get('https://graph.facebook.com/'+get_id+'/accounts?').json()
    print(get_dict_pageid)
    
    if get_dict_pageid['data']:
    
        page_id=(get_dict_pageid['data'][0]['id'])
    
        
        graph = facebook.GraphAPI(access_token=access_token)
        page_access_token = graph.request(page_id, args={'fields': 'access_token'})['access_token']
        print(page_access_token)
        

        req = graph.request(page_id, post_args={'phone':request.form['phone'], 'access_token': page_access_token})
        return render_template('check_page.html',page_id=page_id)
    else:
        return render_template('no_right.html')  


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)


  
