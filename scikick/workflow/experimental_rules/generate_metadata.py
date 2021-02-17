# Write yaml metadata to a shared metadata.yml file

from scikick.config import ScikickConfig
import ruamel.yaml as yaml
import os
skconfig = ScikickConfig()
meta_file = os.path.join(skconfig.report_dir, "metadata.yml")
open(meta_file,"w").write("---\n")
yml_writer = yaml.YAML()
# Use dict() to remove any comments
yml_writer.dump(dict(skconfig.config['yaml_metadata']),
 open(meta_file,"a"))
open(meta_file,"a").write("---\n")

