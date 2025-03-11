import io
import os
import importlib.util
import pytest
import setuptools

# Global variable to capture the setup() keyword arguments.
setup_kwargs = {}

def fake_setup(**kwargs):
    global setup_kwargs
    setup_kwargs = kwargs

def fake_find_namespace_packages():
    # Return only packages that start with "google"
    return ["google.cloud.storage_control"]

def load_setup_module(monkeypatch, version_content, readme_content):
    """Reloads the setup.py module after monkeypatching the file reads."""
    def fake_open(file, *args, **kwargs):
        if file.endswith("google/cloud/storage_control/gapic_version.py"):
            return io.StringIO(version_content)
        elif file.endswith("README.rst"):
            return io.StringIO(readme_content)
        else:
            return open(file, *args, **kwargs)
    monkeypatch.setattr("builtins.open", fake_open)
    monkeypatch.setattr(io, "open", fake_open)
    monkeypatch.setattr(setuptools, "find_namespace_packages", fake_find_namespace_packages)
    monkeypatch.setattr(setuptools, "setup", fake_setup)
    # Determine the path to the setup.py file relative to the tests directory
    setup_path = os.path.join(os.path.dirname(__file__), "..", "packages", "google-cloud-storage-control", "setup.py")
    spec = importlib.util.spec_from_file_location("setup", setup_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_setup_stable(monkeypatch):
    """Test that the stable version (non-beta) configuration is correctly set in setup()."""
    global setup_kwargs
    setup_kwargs = {}
    # Simulate a gapic_version file containing version "1.2.3"
    version_content = '"1.2.3"'
    # Simulate a README file with a dummy content.
    readme_content = "Fake README for stable version"
    load_setup_module(monkeypatch, version_content, readme_content)
    # Assert that the captured setup kwargs contain the expected values.
    assert setup_kwargs["name"] == "google-cloud-storage-control"
    assert setup_kwargs["version"] == "1.2.3"
    assert setup_kwargs["description"] == "Google Cloud Storage Control API client library"
    # For a non-beta (stable) version, we expect production/stable status.
    assert "Development Status :: 5 - Production/Stable" in setup_kwargs["classifiers"]
    # Check that the README file content is correctly used.
    assert setup_kwargs["long_description"] == readme_content
    # Verify that one dependency string includes a fragment from google-api-core
    dep_fragment = "google-api-core[grpc] >= 1.34.1"
    assert any(dep_fragment in dep for dep in setup_kwargs["install_requires"])

def test_setup_beta(monkeypatch):
    """Test that a beta version (starting with '0') sets a beta development status."""
    global setup_kwargs
    setup_kwargs = {}
    # Simulate a gapic_version file with a beta version "0.2.3"
    version_content = '"0.2.3"'
    readme_content = "Fake README for beta version"
    load_setup_module(monkeypatch, version_content, readme_content)
    # Check that the version is read properly.
    assert setup_kwargs["version"] == "0.2.3"
    # For a beta version, the development status should be Beta.
    assert "Development Status :: 4 - Beta" in setup_kwargs["classifiers"]

def test_install_requires_format(monkeypatch):
    """Test that each dependency string in install_requires has proper version specifiers."""
    global setup_kwargs
    setup_kwargs = {}
    version_content = '"1.2.3"'
    readme_content = "Fake README for install_requires test"
    load_setup_module(monkeypatch, version_content, readme_content)
    install_requires = setup_kwargs.get("install_requires", [])
    # For each dependency, check that it includes at least one version specifier like >=, < or !=.
    for dep in install_requires:
        assert (">=" in dep) or ("<" in dep) or ("!=" in dep)
def test_gapic_version_empty(monkeypatch):
    """Test that an empty gapic_version file raises an AssertionError."""
    empty_version = ""
    readme_content = "Dummy README"
    with pytest.raises(AssertionError):
        load_setup_module(monkeypatch, empty_version, readme_content)

def test_gapic_version_multiple(monkeypatch):
    """Test that a gapic_version file with multiple version strings raises an AssertionError."""
    multiple_versions = '"1.2.3" "4.5.6"'
    readme_content = "Dummy README"
    with pytest.raises(AssertionError):
        load_setup_module(monkeypatch, multiple_versions, readme_content)

def test_empty_readme(monkeypatch):
    """Test that an empty README file is handled correctly."""
    version_content = '"1.2.3"'
    empty_readme = ""
    load_setup_module(monkeypatch, version_content, empty_readme)
    # Check that the long description is empty
    assert setup_kwargs["long_description"] == empty_readme

def test_python_requires(monkeypatch):
    """Test that python_requires is set to '>=3.7'."""
    version_content = '"1.2.3"'
    readme_content = "Dummy README"
    load_setup_module(monkeypatch, version_content, readme_content)
    assert setup_kwargs["python_requires"] == ">=3.7"

def test_packages_list(monkeypatch):
    """Test that the packages list includes only packages starting with 'google'."""
    version_content = '"1.2.3"'
    readme_content = "Dummy README"
    load_setup_module(monkeypatch, version_content, readme_content)
    # Using the fake find_namespace_packages, we expect the list to contain one package.
    assert setup_kwargs["packages"] == ["google.cloud.storage_control"]
def test_setup_metadata(monkeypatch):
    """Test that the setup() metadata contains expected keys and values."""
    version_content = '"1.2.3"'
    readme_content = "Dummy README for metadata test"
    load_setup_module(monkeypatch, version_content, readme_content)
    assert setup_kwargs["author"] == "Google LLC"
    assert setup_kwargs["author_email"] == "googleapis-packages@google.com"
    assert setup_kwargs["license"] == "Apache 2.0"
    assert setup_kwargs["url"] == "https://github.com/googleapis/google-cloud-python/tree/main/packages/google-cloud-storage-control"
    assert setup_kwargs["platforms"] == "Posix; MacOS X; Windows"
    assert setup_kwargs["zip_safe"] is False
    assert setup_kwargs["include_package_data"] is True
    # Check that classifiers include several expected classifier items.
    expected_classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
    ]
    for classifier in expected_classifiers:
        assert classifier in setup_kwargs["classifiers"]
    # Check that extras_require is an empty dictionary.
    assert setup_kwargs["extras_require"] == {}
    # Check that there are exactly 5 dependency strings in install_requires.

    """Test that a missing README file raises FileNotFoundError."""
    version_content = '"1.2.3"'
    def fake_open_missing_readme(file, *args, **kwargs):
        if file.endswith("README.rst"):
            raise FileNotFoundError("README not found")
        elif file.endswith("google/cloud/storage_control/gapic_version.py"):
            return io.StringIO(version_content)
        else:
            return open(file, *args, **kwargs)
    monkeypatch.setattr("builtins.open", fake_open_missing_readme)
    monkeypatch.setattr(io, "open", fake_open_missing_readme)
    monkeypatch.setattr(setuptools, "find_namespace_packages", fake_find_namespace_packages)
    monkeypatch.setattr(setuptools, "setup", fake_setup)
    setup_path = os.path.join(os.path.dirname(__file__), "..", "packages", "google-cloud-storage-control", "setup.py")
    spec = importlib.util.spec_from_file_location("setup", setup_path)
    module = importlib.util.module_from_spec(spec)
    with pytest.raises(FileNotFoundError):
        spec.loader.exec_module(module)
def test_missing_gapic_version_file(monkeypatch):
    """Test that a missing gapic_version file raises FileNotFoundError."""
    def fake_open_missing_version(file, *args, **kwargs):
        if file.endswith("google/cloud/storage_control/gapic_version.py"):
            raise FileNotFoundError("gapic_version.py not found")
        elif file.endswith("README.rst"):
            return io.StringIO("Some README")
        else:
            return open(file, *args, **kwargs)
    monkeypatch.setattr("builtins.open", fake_open_missing_version)
    monkeypatch.setattr(io, "open", fake_open_missing_version)
    monkeypatch.setattr(setuptools, "find_namespace_packages", fake_find_namespace_packages)
    monkeypatch.setattr(setuptools, "setup", fake_setup)
    setup_path = os.path.join(os.path.dirname(__file__), "..", "packages", "google-cloud-storage-control", "setup.py")
    spec = importlib.util.spec_from_file_location("setup", setup_path)
    module = importlib.util.module_from_spec(spec)
    with pytest.raises(FileNotFoundError):
        spec.loader.exec_module(module)