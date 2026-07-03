# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Unit tests for tool call validation logic."""

from agents.scripts.validate_tool_call import is_destructive


def test_is_destructive_blocked():
    # Destructive Unix commands
    assert is_destructive("rm -rf /") is True
    assert is_destructive("rm -fr /") is True
    assert is_destructive("rm -rf /*") is True
    assert is_destructive("rm -rf /etc") is True
    assert is_destructive("rm -rf /usr/bin") is True
    assert is_destructive("sudo rm -rf /") is True
    assert is_destructive("rm --recursive --force /") is True
    assert is_destructive("FOO=bar rm -rf /") is True

    # Nested / chained destructive commands
    assert is_destructive("git add . && rm -rf /") is True
    assert is_destructive("rm -rf /; echo done") is True

    # Destructive Windows commands
    assert is_destructive("rd /s /q c:\\") is True
    assert is_destructive("rmdir /s /q c:\\windows") is True
    assert is_destructive("del /f /s /q c:\\*") is True


def test_is_destructive_allowed():
    # Safe Unix commands
    assert is_destructive("rm -rf /tmp/my_temp_dir") is False
    assert is_destructive("rm -rf ./my_project") is False
    assert is_destructive("ls -la") is False
    assert is_destructive("echo 'rm -rf /'") is False
    assert is_destructive("git commit -m \"fix rm -rf / in code\"") is False

    # Safe Windows commands
    assert is_destructive("del my_file.txt") is False
    assert is_destructive("rmdir /s /q my_dir") is False
