# server_monitoring

### Set your serever at .zshrc
```bash
alias open{server_ID_0}='ssh -P {Port number_0} user_ID@server_IP_0'
alias open{server_ID_1}='ssh -P {Port number_1} user_ID@server_IP_1'
alias open{server_ID_2}='ssh -P {Port number_2} user_ID@server_IP_2'
```

Formats that use alias are examples only. You only need to have ‘ssh’ or less in your .zshrc.

The open{server_ID} is intended to be used like a shorthand.

### Requirements
```bash
pip install paramiko==3.4.0
pip install rich==13.7.0
pip install python-dotenv==1.0.1 
```

### Run
```bash
python server_monitor.py

Enter server password: {Passward}
```

The password should be the same on all servers.