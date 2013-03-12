Duplicator
-----

Duplicator is a tiny udp server for duplicating metrics for Bucky.

Config File Options
-------------------

The configuration file is a normal Python file that defines a number of
variables. 

	log_level = "INFO"

	input_ip = "0.0.0.0"
	input_port = 8125 

	output_ip = "0.0.0.0"
	output_ports = [8126,8127]
