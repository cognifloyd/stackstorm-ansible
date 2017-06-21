#!/usr/bin/env python

from __future__ import print_function

import os
import subprocess
import re
import sys

from lib.ansible_base import AnsibleBaseRunner

__all__ = [
    'AnsiblePlaybookRunner'
]


class AnsiblePlaybookRunner(AnsibleBaseRunner):
    """
    Runs Ansible playbook.
    See: http://docs.ansible.com/playbooks.html
    """
    BINARY_NAME = 'ansible-playbook'
    REPLACEMENT_RULES = {
        '--verbose=vvvv': '-vvvv',
        '--verbose=vvv': '-vvv',
        '--verbose=vv': '-vv',
        '--verbose=v': '-v',
        '--become_method': '--become-method',
        '--become_user': '--become-user',
        '--flush_cache': '--flush-cache',
        '--force_handlers': '--force-handlers',
        '--inventory_file': '--inventory-file',
        '--list_hosts': '--list-hosts',
        '--list_tags': '--list-tags',
        '--list_tasks': '--list-tasks',
        '--module_path': '--module-path',
        '--private_key': '--private-key',
        '--skip_tags': '--skip-tags',
        '--start_at_task': '--start-at-task',
        '--syntax_check': '--syntax-check',
        '--vault_password_file': '--vault-password-file',
    }

    def __init__(self, *args, **kwargs):
        super(AnsiblePlaybookRunner, self).__init__(*args, **kwargs)

    def handle_json_arg(self):
        os.environ['ANSIBLE_CALLBAKC_PLUGIN'] = 'json'
        self.stdout = subprocess.PIPE
        # TODO: --json is probably not be compatible with other options
        # like syntax-check, verbose, and possibly others

    def popen_call(self, p):
        """
        :param subprocess.Popen p:
        :return:
        """
        if not self.json_output:
            return super(AnsiblePlaybookRunner, self).popen_call(p)

        # lines that should go to stderr instead of stdout
        stderr_lines = re.compile(
            r'('

            # these were identified in this closed PR:
            #    https://github.com/ansible/ansible/pull/17448/files
            # see https://github.com/ansible/ansible/issues/17122
            r"^\tto retry, use: --limit @.*$"
            r'|'
            r"^skipping playbook include '.*' due to conditional test failure$"
            r'|'
            r"^statically included: .*$"

            # other possibilities:
            # r'|'
            # r'^to see the full traceback, use -vvv$'
            # r'|'
            # r"^The full traceback was:$"
            # but then I would somehow have to include the traceback as well...

            r')'
        )

        while p.poll() is None:
            line = p.stdout.readline()
            if re.match(stderr_lines, line):
                print(line, file=sys.stderr)
            else:
                print(line)

        return p.returncode


if __name__ == '__main__':
    AnsiblePlaybookRunner(sys.argv).execute()
