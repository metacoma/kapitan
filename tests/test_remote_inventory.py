import os
import sys
import unittest
import tempfile
from shutil import rmtree, copytree
from distutils.dir_util import copy_tree
from kapitan.cached import reset_cache
from kapitan.cli import main
from kapitan.remoteinventory.fetch import (
    fetch_git_source,
    fetch_git_inventories,
    fetch_http_source,
    fetch_http_inventories,
)
from kapitan.dependency_manager.base import DEPENDENCY_OUTPUT_CONFIG


class RemoteInventoryTest(unittest.TestCase):
    def setUp(self):
        os.chdir(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "test_remote_inventory", "environment_one"
            )
        )

    def test_fetch_git_inventory(self):
        temp_dir = tempfile.mkdtemp()
        git_source = "https://github.com/deepmind/kapitan.git"
        fetch_git_source(git_source, temp_dir)
        self.assertTrue(os.path.isdir(os.path.join(temp_dir, "kapitan.git", "kapitan")))
        rmtree(temp_dir)

    def test_clone_inv_subdir(self):
        temp_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        git_source = "https://github.com/deepmind/kapitan.git"
        inv = [{"output_path": os.path.join(output_dir, "subdir"), "ref": "master", "subdir": "tests"}]
        fetch_git_inventories((git_source, inv), "./inventory", temp_dir)
        self.assertTrue(os.path.isdir(os.path.join(output_dir, "subdir")))
        rmtree(output_dir)
        rmtree(temp_dir)

    def test_fetch_http_inventory(self):
        temp_dir = tempfile.mkdtemp()

        http_sources = [
            "https://github.com/deepmind/kapitan/raw/master/tests/test_remote_inventory/zipped_inventories/inventory.7z",
            "https://raw.githubusercontent.com/deepmind/kapitan/master/tests/test_resources/inventory/classes/common.yml",
            "https://github.com/deepmind/kapitan/raw/master/tests/test_remote_inventory/zipped_inventories/inventory.zip",
        ]
        for source in http_sources:
            fetch_http_source(source, temp_dir)
        self.assertTrue(os.path.isfile(os.path.join(temp_dir, "47c29a3binventory.7z")))
        # self.assertTrue(os.path.isfile(os.path.join(temp_dir,"009a21cfmaster.zip")))
        self.assertTrue(os.path.isfile(os.path.join(temp_dir, "eac6ceb7common.yml")))
        self.assertTrue(os.path.isfile(os.path.join(temp_dir, "47c29a3binventory.zip")))
        rmtree(temp_dir)

    def test_unpack_http_inv(self):
        temp_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        http_source = "https://github.com/deepmind/kapitan/raw/master/tests/test_remote_inventory/zipped_inventories/inventory.tar.gz"
        inv = [{"output_path": os.path.join(output_dir, "subdir"), "unpack": "True"}]
        fetch_http_inventories((http_source, inv), "./inventory", temp_dir)

        self.assertTrue(os.path.isdir(os.path.join(output_dir, "subdir", "targets")))
        rmtree(temp_dir)
        rmtree(output_dir)

    def test_compile_fetch(self):
        temp_output = tempfile.mkdtemp()
        temp_inv = tempfile.mkdtemp()

        copy_tree(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                "test_remote_inventory",
                "environment_one",
                "inventory",
            ),
            temp_inv,
        )
        sys.argv = [
            "kapitan",
            "compile",
            "--fetch",
            "--output-path",
            temp_output,
            "--inventory-path",
            temp_inv,
            "--targets",
            "remoteinv-example",
            # "remoteinv-nginx",
            "zippedinv",
        ]
        main()

        self.assertTrue(os.path.isfile(os.path.join(temp_inv, "targets", "remoteinv-nginx.yml")))
        self.assertTrue(os.path.isfile(os.path.join(temp_inv, "targets", "nginx.yml")))
        self.assertTrue(os.path.isfile(os.path.join(temp_inv, "targets", "nginx-dev.yml")))
        # self.assertTrue(os.path.isdir(os.path.join(temp_output, "compiled", "remoteinv-nginx")))
        self.assertTrue(os.path.isdir(os.path.join(temp_output, "compiled", "zippedinv")))

        rmtree(temp_inv)
        rmtree(temp_output)

    def tearDown(self):
        os.chdir("../../../")
        reset_cache()


if __name__ == "__main__":
    unittest.main()
