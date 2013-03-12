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
import multiprocessing
import Queue
import signal
import sys

import duplicator
import duplicator.cfg as cfg 
import duplicator.udpserver as udpserver
import duplicator.client as client
log = logging.getLogger(__name__)

__usage__ = "%prog [OPTIONS]"
__version__ = "duplicator %s" % duplicator.__version__

def main():  
    # Logging have to be configured before load_config,
    # where it can (and should) be already used
    logfmt = "[%(levelname)s] %(module)s - %(message)s"
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(logfmt))
    handler.setLevel(logging.ERROR) # Overridden by configuration
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.DEBUG)

    
    cfgfile = sys.argv[1]
    
    load_config(cfgfile, True)

    handler.setLevel(cfg.log_level)
   
    sampleq = multiprocessing.Queue()
    server = udpserver.UDPServer(cfg.input_ip,cfg.input_port,sampleq)
    server.start()
    
    clients = []
    for client_port in cfg.output_ports:        
        send, recv = multiprocessing.Pipe()
        instance = client.Client(cfg.output_ip,client_port, recv)
        instance.start()
        clients.append((instance, send))

    def shutdown(signum, frame):        
        server.close()
        sampleq.put(None)

    signal.signal(signal.SIGTERM, shutdown)

    while True:
        try:
            sample = sampleq.get(True, 1)
            if not sample:
                break
            for instance, pipe in clients:
                if not instance.is_alive():
                    log.error("Client process died. Exiting.")
                    sys.exit(1)
                pipe.send(sample)
        except Queue.Empty:
            pass        
        if not server.is_alive():
            log.error("Server thread died. Exiting.")
            sys.exit(1)

    for child in multiprocessing.active_children():
        child.terminate()
        child.join()
    sys.exit()


def load_config(cfgfile, full_trace=False):
    cfg_mapping = vars(cfg)
    try:
        if cfgfile is not None:
            execfile(cfgfile, cfg_mapping)
    except Exception, e:
        log.error("Failed to read config file: %s" % cfgfile)
        if full_trace:
            log.exception("Reason: %s" % e)
        else:
            log.error("Reason: %s" % e)
        sys.exit(1)
    for name in dir(cfg):
        if name.startswith("_"):
            continue
        if name in cfg_mapping:
            setattr(cfg, name, cfg_mapping[name])


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception, e:
        raise
        print e
