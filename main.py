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
        try:
            self.client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                pkey=self.private_key,
                allow_agent=False,
                look_for_keys=False
            )
        except paramiko.AuthenticationException:
            print('Authentication failed, please verify your credentials.')
            sys.exit(1)
        except paramiko.SSHException as sshe:
            print('Could not establish SSH connection: {}'.format(sshe))
            sys.exit(1)
        except Exception as e:
            print('Something else went wrong: {}'.format(e))
            sys.exit(1)

    def run(self, cmd, timeout=1800):
        stdin, stdout, stderr = self.client.exec_command(cmd, timeout=timeout)
        stdout = stdout.read().decode('utf-8')
        stderr = stderr.read().decode('utf-8')
        return stdout, stderr

    def disconnect(self):
        self.client.close()


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
            print ("Running on {}\n".format(machine.hostname))
            machine.connect()
            for cmd in self.commands:
                out, err = machine.run(cmd)
                print("STDOUT: ", out)
                print("STDERR: ", err)
            machine.disconnect()

    def load_commands_from_file(self, path):
        if not os.path.exists(path):
            print("No such file: {}".format(path))
            sys.exit(1)

        with open(path, 'r') as f:
            content = f.readlines()
        content = [c.strip('\n') for c in content]
        self.commands = content

    def load_commands(self, commands):
        self.commands = commands


if __name__ == "__main__":
    baseliner = BlackSwanBaseliner()

    # Add machines
    baseliner.add_machine('ms1126.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    baseliner.add_machine('ms1139.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    baseliner.add_machine('ms1124.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    baseliner.add_machine('ms1134.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    baseliner.add_machine('ms1120.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    baseliner.add_machine('ms1110.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    baseliner.add_machine('ms1129.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    baseliner.add_machine('ms1112.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    baseliner.add_machine('ms1137.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')
    baseliner.add_machine('ms1103.utah.cloudlab.us', 22, 'noobjc', os.path.expanduser('~/.ssh/id_rsa_cloudlab'), '12345')

    baseliner.load_commands_from_file('commands.txt')
    baseliner.run()
