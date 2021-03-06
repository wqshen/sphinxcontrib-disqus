"""Test extension with regular sphinx-build command."""

from subprocess import CalledProcessError, check_output, STDOUT

import py
import pytest

BASE_CONFIG = """\
import sys
sys.path.append('{}')
extensions = ['sphinxcontrib.disqus']
master_doc = 'index'
nitpicky = True
"""

SHORTNAME_PARAMS = [
    ("disqus_shortname = 'good'", ''),
    ('', 'disqus_shortname config value must be set for the disqus extension to work.'),
    ("disqus_shortname = ''", 'disqus_shortname config value must be set for the disqus extension to work.'),
    ("disqus_shortname = 'B@D'", 'disqus_shortname config value must be 3-50 letters, numbers, and hyphens only.'),
]


@pytest.mark.parametrize('tail,expected_error', SHORTNAME_PARAMS)
def test_shortname(tmpdir, tail, expected_error):
    """Test working and errors for disqus_shortname configuration."""
    tmpdir.join('conf.py').write(BASE_CONFIG.format(py.path.local(__file__).join('..', '..')))
    tmpdir.join('conf.py').write(tail, mode='a')
    tmpdir.join('index.rst').write('====\nMain\n====\n\n.. toctree::\n    :maxdepth: 2\n.. disqus::')

    command = ['sphinx-build', '-W', '-b', 'html', '.', '_build/html']
    if expected_error:
        with pytest.raises(CalledProcessError) as exc:
            check_output(command, cwd=str(tmpdir), stderr=STDOUT)
        error_message = exc.value.output.decode('utf-8')
        assert expected_error in error_message
    else:
        check_output(command, cwd=str(tmpdir))


@pytest.mark.parametrize('rst_title', ['====\nMain\n====\n\n', ''])
def test_identifier(tmpdir, rst_title):
    """Test working and errors for disqus_identifier configuration."""
    tmpdir.join('conf.py').write(BASE_CONFIG.format(py.path.local(__file__).join('..', '..')))
    tmpdir.join('conf.py').write("disqus_shortname = 'good'", mode='a')
    tmpdir.join('index.rst').write('{}.. toctree::\n    :maxdepth: 2\n.. disqus::'.format(rst_title))

    command = ['sphinx-build', '-b', 'html', '.', '_build/html']
    if not rst_title:
        with pytest.raises(CalledProcessError) as exc:
            check_output(command, cwd=str(tmpdir), stderr=STDOUT)
        error_message = exc.value.output.decode('utf-8')
        expected_error = 'No title nodes found in document, cannot derive disqus_identifier config value.'
        assert expected_error in error_message
    else:
        stdout = check_output(command, cwd=str(tmpdir), stderr=STDOUT).decode('utf-8')
        html_body = tmpdir.join('_build', 'html', 'index.html').read()
        assert 'warning' not in stdout
        assert 'id="disqus_thread"' in html_body
        assert 'data-disqus-identifier="Main"' in html_body
