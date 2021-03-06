# -*- coding: utf-8 -
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import logging
import socket
import sys
import multiprocessing

try:
    import cPickle as pickle
except ImportError:
    import pickle

log = logging.getLogger(__name__)

class Client(multiprocessing.Process): 
    def __init__(self, ip, port, pipe): 
        super(Client, self).__init__()
        self.daemon = True
        self.ip = ip
        self.port = port
        self.pipe = pipe        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def close(self):
        try:
            self.sock.close()
        except:
            pass
          
    def run(self):
        while True:
            self.send(*self.pipe.recv())
            
    def send(self, data, addr):
        try:
            log.debug("Sending UDP packet to %s:%s" % (self.ip, self.port))
            self.sock.sendto(data,(self.ip, self.port))
        except:
            log.exception("Error sending to %s:%s." % addr)
