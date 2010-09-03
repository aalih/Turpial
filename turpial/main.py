#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Controlador de Turpial'''

#
# Author: Wil Alvarez (aka Satanas)
# Nov 8, 2009

import os
import sys
import base64
import logging
from optparse import OptionParser

path = os.environ['PATH'].split(';')
path.insert(0, 'lib')
os.environ['PATH'] = ';'.join(path)

from turpial.ui.gtk.main import Main as _GTK
from turpial.api.services import HTTPServices
from turpial.api.turpialapi import TurpialAPI
from turpial.config import ConfigHandler, ConfigApp

class Turpial:
    '''Inicio de Turpial'''
    def __init__(self):
        parser = OptionParser()
        parser.add_option('-d', '--debug', dest='debug', action='store_true',
            help='Debug Mode', default=False)
        parser.add_option('-i', '--interface', dest='interface',
            help='Select interface to use. (cmd|gtk)', default='gtk')
        parser.add_option('-c', '--clean', dest='clean', action='store_true',
            help='Clean all bytecodes', default=False)
        parser.add_option('--test', dest='test', action='store_true',
            help='Test mode. Only load timeline', default=False)
        
        (options, _) = parser.parse_args()
        
        self.config = None
        self.global_cfg = ConfigApp()
        self.profile = None
        self.remember = False
        self.testmode = options.test
        self.httpserv = None
        self.api = None
        
        if options.debug: 
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('Controller')
        
        if options.clean:
            self.__clean()
            self.signout()
            
        self.interface = options.interface
        if options.interface == 'gtk+':
            self.ui = _GTK(self, extend=True)
        elif options.interface == 'gtk':
            self.ui = _GTK(self)
        else:
            print 'No existe tal interfaz. Saliendo...'
            sys.exit(-1)
        
        self.httpserv = HTTPServices()
        self.api = TurpialAPI()
        
        self.log.debug('Iniciando Turpial')
        self.httpserv.start()
        self.api.start()
        self.api.change_api_url(self.global_cfg.read('Proxy', 'url'))

        if self.testmode:
            self.log.debug('Modo Pruebas Activado')
            
        self.ui.show_login(self.global_cfg)
        self.ui.main_loop()
        
    def __clean(self):
        '''Limpieza de ficheros .pyc y .pyo'''
        self.log.debug("Limpiando la casa...")
        i = 0
        for root, dirs, files in os.walk('.'):
            for f in files:
                path = os.path.join(root, f)
                if path.endswith('.pyc') or path.endswith('.pyo'): 
                    self.log.debug("Borrado %s" % path)
                    os.remove(path)
            
    def __validate_signin(self, val):
        '''Chequeo de inicio de sesion'''
        if val.has_key('error'):
            self.ui.cancel_login(val['error'])
        else:
            self.profile = val
            self.ui.update_user_profile(val)
            self.ui.show_main(self.config, self.global_cfg, val)
            
            self._update_timeline()
            if self.testmode: return
            self._update_replies()
            self._update_directs()
            self._update_favorites()
            self._update_rate_limits()
            
    def __validate_credentials(self, val):
        '''Chequeo de credenciales'''
        if val.has_key('error'):
            self.ui.cancel_login(val['error'])
        else:
            if self.api.has_oauth_support():
                self.api.validate_credentials(self.__signin_done)
            else:
                self.api.is_oauth = False
                self.__signin_done(None, None, None)
    
    def __done_follow(self, friends, profile, user, follow):
        self.ui.update_user_profile(profile)
        self.ui.update_friends(friends)
        self.ui.update_follow(user, follow)
        #self.ui.update_timeline(friends)
        
    def __direct_done(self, tweet):
        self.ui.tweet_done(tweet)
        
    def __tweet_done(self, tweet):
        if tweet:
            self.profile['statuses_count'] += 1
            self.ui.update_user_profile(self.profile)
        self.ui.tweet_done(tweet)
        
    def __signin_done(self, val):
        '''Inicio de sesion finalizado'''
        if val.has_key('error'):
            self.ui.cancel_login(val['error'])
        else:
            self.profile = val
            self.config = ConfigHandler(val['screen_name'])
            if self.remember:
                self.global_cfg.write('Login', 'username', self.api.username)
                self.global_cfg.write('Login', 'password',
                    base64.b64encode(self.api.password))
            else:
                self.global_cfg.write('Login', 'username', '')
                self.global_cfg.write('Login', 'password', '')
            
            self.httpserv.update_img_dir(self.config.imgdir)
            self.httpserv.set_credentials(self.api.username, self.api.password)
        
            self.api.muted_users = self.config.load_muted_list()
            
            self.ui.show_main(self.config, self.global_cfg, self.profile)
            self._update_timeline()
            if self.testmode: return
            self._update_replies()
            self._update_directs()
            self._update_rate_limits()
            self._update_favorites()
            self._update_friends()
        
    def _update_timeline(self):
        '''Actualizar linea de tiempo'''
        self.ui.start_updating_timeline()
        tweets = int(self.config.read('General', 'num-tweets'))
        self.api.update_timeline(self.ui.update_timeline, tweets)
        
    def _update_replies(self):
        '''Actualizar numero de respuestas'''
        self.ui.start_updating_replies()
        tweets = int(self.config.read('General', 'num-tweets'))
        self.api.update_replies(self.ui.update_replies, tweets)
        
    def _update_directs(self):
        '''Actualizar mensajes directos'''
        self.ui.start_updating_directs()
        tweets = int(self.config.read('General', 'num-tweets'))
        self.api.update_directs(self.ui.update_directs, tweets)
        
    def _update_favorites(self):
        '''Actualizar favoritos'''
        self.api.update_favorites(self.ui.update_favorites)
    
    def _update_rate_limits(self):
        self.api.update_rate_limits(self.ui.update_rate_limits)
        
    def _update_friends(self):
        '''Actualizar amigos'''
        self.api.get_friends(self.ui.update_friends)
        
    def signin(self, username, password):
        self.config = ConfigHandler(username)
        self.api.auth(username, password, self.__validate_signin)
        
    def signin_oauth(self, username, password, remember):
        self.remember = remember
        self.api.auth(username, password, self.__validate_credentials)
        
    def auth_token(self, pin):
        self.api.authorize_oauth_token(pin, self.__signin_done)
        
    def signout(self):
        '''Finalizar sesion'''
        self.save_muted_list()
        self.log.debug('Desconectando')
        if self.httpserv:
            self.httpserv.quit()
            self.httpserv.join()
        if self.api: 
            self.api.quit()
            self.api.join()
        sys.exit(0)
    
    def update_status(self, text, reply_id=None):
        if text.startswith('D '):
            self.api.update_status(text, reply_id, self.__direct_done)
        else:
            self.api.update_status(text, reply_id, self.__tweet_done)
        
    def destroy_status(self, tweet_id):
        self.api.destroy_status(tweet_id, self.ui.after_destroy)
        
    def set_favorite(self, tweet_id):
        self.api.set_favorite(tweet_id, self.ui.update_favorites)
        
    def unset_favorite(self, tweet_id):
        self.api.unset_favorite(tweet_id, self.ui.update_favorites)
    
    def retweet(self, tweet_id):
        self.api.retweet(tweet_id, self.ui.tweet_changed)
    
    def follow(self, user):
        self.api.follow(user, self.__done_follow)
        
    def unfollow(self, user):
        self.api.unfollow(user, self.__done_follow)
        
    def update_profile(self, new_name, new_url, new_bio, new_location):
        self.api.update_profile(new_name, new_url, new_bio, new_location,
            self.ui.update_user_profile)
    
    def in_reply_to(self, twt_id):
        self.api.in_reply_to(twt_id, self.ui.update_in_reply_to)
        
    def get_conversation(self, twt_id):
        self.api.get_conversation(twt_id, self.ui.update_conversation)
        
    def mute(self, user):
        self.ui.start_updating_timeline()
        self.api.mute(user, self.ui.update_timeline)
        
    def short_url(self, text, callback):
        service = self.config.read('Services', 'shorten-url')
        self.httpserv.short_url(service, text, callback)
    
    def download_user_pic(self, user, pic_url, callback):
        self.httpserv.download_pic(user, pic_url, callback)
        
    def upload_pic(self, path, callback):
        service = self.config.read('Services', 'upload-pic')
        self.httpserv.upload_pic(service, path, callback)
        
    def search_topic(self, query):
        self.ui.start_search()
        self.api.search_topic(query, self.ui.update_search_topics)
        
    def get_popup_info(self, tweet_id, user):
        if tweet_id in self.api.to_fav:
            return {'busy': 'Marcando favorito...'}
        elif tweet_id in self.api.to_unfav:
            return {'busy': 'Desmarcando favorito...'}
        elif tweet_id in self.api.to_del:
            return {'busy': 'Borrando...'}
            
        rtn = {}
        if self.api.friendsloaded:
            rtn['friend'] = self.api.is_friend(user)

        rtn['fav'] = self.api.is_fav(tweet_id)
        rtn['own'] = (self.profile['screen_name'] == user)
        
        return rtn
        
    def save_config(self, config, update):
        self.config.save(config)
        if update:
            self.ui.update_config(self.config)
            
    def save_global_config(self, config):
        self.global_cfg.save(config)
        
    def save_muted_list(self):
        if self.config:
            self.config.save_muted_list(self.api.muted_users)
        
    def get_muted_list(self):
        return self.api.get_muted_list()
            
    def update_muted(self, muted_users):
        self.ui.start_updating_timeline()
        timeline = self.api.mute(muted_users, self.ui.update_timeline)
        
    def destroy_direct(self, tweet_id):
        self.api.destroy_direct(tweet_id, self.ui.after_destroy)
        
    def get_friends(self):
        return self.api.get_single_friends_list()
        
if __name__ == '__main__':
    t = Turpial()
