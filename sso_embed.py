import urllib
import base64
import json
import time
import binascii
import os
from hashlib import sha1
import six
import six.moves.urllib as urllib
import hmac

def to_ascii(s):
  """Compatibility function for converting between Python 2.7 and 3 calls"""
  if isinstance(s, six.text_type):
    return s
  elif isinstance(s, six.binary_type):
    return "".join(map(chr, map(ord, s.decode(encoding='UTF-8'))))
  return s

class Looker:
  def __init__(self, host, secret):
    self.secret = secret
    self.host = host


class User:
  def __init__(self, id=id, first_name=None, last_name=None,
               permissions=[], models=[], group_ids=[], external_group_id=None,
               user_attributes={}, access_filters={}):
    self.external_user_id = json.dumps(id)
    self.first_name = json.dumps(first_name)
    self.last_name = json.dumps(last_name)
    self.permissions = json.dumps(permissions)
    self.models = json.dumps(models)
    self.access_filters = json.dumps(access_filters)
    self.user_attributes = json.dumps(user_attributes)
    self.group_ids = json.dumps(group_ids)
    self.external_group_id = json.dumps(external_group_id)


class URL:
  def __init__(self, looker, user, session_length, embed_url, force_logout_login=False):
    self.looker = looker
    self.user = user
    self.path = '/login/embed/' + urllib.parse.quote_plus(embed_url)
    self.session_length = json.dumps(session_length)
    self.force_logout_login = json.dumps(force_logout_login)

  def set_time(self):
    self.time = json.dumps(int(time.time()))

  def set_nonce(self):
    self.nonce = json.dumps(to_ascii(binascii.hexlify(os.urandom(16))))

  def sign(self):
    #  Do not change the order of these
    string_to_sign = "\n".join([self.looker.host,
                                self.path,
                                self.nonce,
                                self.time,
                                self.session_length,
                                self.user.external_user_id,
                                self.user.permissions,
                                self.user.models,
                                self.user.group_ids,
                                self.user.external_group_id,
                                self.user.user_attributes,
                                self.user.access_filters])

    signer = hmac.new(bytearray(self.looker.secret, 'UTF-8'), string_to_sign.encode('UTF-8'), sha1)
    self.signature = base64.b64encode(signer.digest())

  def to_string(self):
    self.set_time()
    self.set_nonce()
    self.sign()

    params = {'nonce':               self.nonce,
              'time':                self.time,
              'session_length':      self.session_length,
              'external_user_id':    self.user.external_user_id,
              'permissions':         self.user.permissions,
              'models':              self.user.models,
              'group_ids':           self.user.group_ids,
              'external_group_id':   self.user.external_group_id,
              'user_attributes':     self.user.user_attributes,
              'access_filters':      self.user.access_filters,
              'signature':           self.signature,
              'first_name':          self.user.first_name,
              'last_name':           self.user.last_name,
              'force_logout_login':  self.force_logout_login}

    query_string = '&'.join(["%s=%s" % (key, urllib.parse.quote_plus(val)) for key, val in params.items()])

    return "%s%s?%s" % (self.looker.host, self.path, query_string)

embed_secret='**Place your embed secret here**'
def test():
  looker = Looker('localhost:9999', embed_secret)


  user = User(88,
              first_name='Foo',
              last_name='Bar',
              permissions=['see_lookml_dashboards', 'access_data','see_user_dashboards','see_looks','explore','see_sql','see_user_dashboards','embed_browse_spaces','save_content'],
              models=['sso_demo'],
              group_ids=[5,6,9],
              external_group_id='Publisher1',
              user_attributes={"brand": "Levi's,Calvin Klein,Dockers", "state": "California,Nevada,Colorado"},
              access_filters={'fake_model': {'id': 1}})

  fifteen_minutes = 15 * 60

  url = URL(looker, user, fifteen_minutes, "/embed/dashboards/11", force_logout_login=True)

  print ("https://" + url.to_string())

  return "https://" + url.to_string()

test()
  


  
