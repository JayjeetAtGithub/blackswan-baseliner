import os
import sys

import paramiko


class Machine(object):
    def __init__(self, hostname, port, username, private_key_file, passphrase):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.private_key_file = private_key_file
        self.passphrase = passphrase
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.private_key = paramiko.RSAKey.from_private_key_file(
            private_key_file, password=passphrase)

    def connect(self):
        self.client.connect(
            hostname=self.hostname, 
            port=self.port, 
            username=self.username, 
            pkey=self.private_key,
            allow_agent=False, 
            look_for_keys=False
        )

    def run(self, cmd, timeout=10):
        stdin, stdout, stderr = self.client.exec_command(cmd, timeout=timeout)
        stdout = stdout.read().decode('utf-8')
        stderr = stderr.read().decode('utf-8')
        return stdout, stderr


class BlackSwanBaseliner(object):
    def __init__(self):
        self.machines = list()
        self.commands = list()

    def add_machine(self, hostname, port, username, private_key_file, passphrase):
        self.machines.append(Machine(
            hostname,
            port,
            username,
            private_key_file,
            passphrase
        ))
        return len(self.machines)

    def run(self):
        for machine in self.machines:
            machine.connect()
            for cmd in self.commands:
                out, err = machine.run(cmd)
                print("STDOUT: ", out)
                print("STDERR: ", err)

    def load_commands_from_file(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError("No such file at {}".format(path))
        with open(path, 'r') as f:
            content = f.readlines()
        content = [c.strip('\n') for c in content]
        self.commands = content

    def load_commands(self, commands):
        self.commands = commands


if __name__ == "__main__":
    baseliner = BlackSwanBaseliner()
    baseliner.add_machine('ms1137.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    baseliner.add_machine('hp125.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    # baseliner.load_commands_from_file('commands.txt')
    baseliner.load_commands(['ls -al'])
    baseliner.run()
