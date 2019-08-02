import responder
import docker

class DockerHandler:
  def __init__(self):
    self._client = docker.from_env()

  def _get_all_stack_filter(self):
    # https://github.com/docker/cli/blob/8b9cdab4e6f4a505bf36e300c4ad738421285fe7/cli/compose/convert/compose.go#L15
    # https://github.com/docker/cli/blob/ae1618713f83e7da07317d579d0675f578de22fa/cli/command/stack/swarm/common.go#L30
    return {"label": "com.docker.stack.namespace"}

  def _get_stack_filter(self, namespace):
    # https://github.com/docker/cli/blob/ae1618713f83e7da07317d579d0675f578de22fa/cli/command/stack/swarm/common.go#L14
    return {"label": "com.docker.stack.namespace={0}".format(namespace)}

  def _get_all_stack_services(self):
    # https://github.com/docker/cli/blob/0904fbfc77dbd4b6296c56e68be573b889d049e3/cli/command/stack/swarm/list.go#L17
    return self._client.services.list(filters = self._get_all_stack_filter())

  def _get_stack_services(self, namespace):
    # https://github.com/docker/cli/blob/0904fbfc77dbd4b6296c56e68be573b889d049e3/cli/command/stack/swarm/list.go#L17
    return self._client.services.list(filters = self._get_stack_filter(namespace))

  def _get_stack_ps(self, namespace):
    # https://github.com/docker/cli/blob/ae1618713f83e7da07317d579d0675f578de22fa/cli/command/stack/swarm/ps.go#L20
    # https://github.com/docker/docker-py/blob/17c86429e454e65f74660393ffb427adb8db154a/docker/models/services.py#L54
    return self._client.api.tasks(filters = self._get_stack_filter(namespace))

  def _remove_services(self, services):
    # https://github.com/docker/cli/blob/ae1618713f83e7da07317d579d0675f578de22fa/cli/command/stack/swarm/remove.go#L86
    for service in services:
      service.remove()

  def _get_node_ids_for(self, namespace):
    ps = self._get_stack_ps(namespace)
    return frozenset(map(lambda task: task['NodeID'], ps))

  def _remove_volumes_for(self, namespace, node_ids):
    for node_id in node_ids:
      node = self._client.nodes.get(node_id)
      hostname = node.attrs['Description']['Hostname']
      import subprocess
      subprocess.run(['docker', '-H', hostname, 'volume', 'rm', '{}_workspace-data'.format(namespace)], check=True)


  def list_workspaces(self):
    stack_services = self._get_all_stack_services()
    labels = frozenset(map(lambda service: service.attrs['Spec']['Labels']['com.docker.stack.namespace'], stack_services))
    return labels - frozenset(('reverse_proxy', 'admin'))

  def show_workspace(self, name):
    stack_services = self._get_stack_services(name)
    labels = frozenset(map(lambda service: service.attrs['Spec']['Labels']['com.docker.stack.namespace'], stack_services))
    if len(labels - frozenset(('reverse_proxy', 'admin'))) == 0:
      return None
    else:
      return name

  def add_workspace(self, name):
    import re
    if re.match(r'^[a-z0-9]+(-[a-z0-9]+)?$', name):
      from urllib.request import urlopen
      import os
      url = os.getenv('C9_WORKSPACE_DOCKER_COMPOSE_URL', 'https://raw.githubusercontent.com/YusukeIwaki/cloud-pine/master/workspace/docker-compose.yml')
      raw_compose_file = urlopen(url).read()

      import subprocess
      subprocess.run(['docker', 'stack', 'deploy', '--compose-file', '-', name], input = raw_compose_file, check=True)

  def remove_workspace(self, name):
    if name == 'reverse_proxy' or name == 'admin':
      return
    import re
    if re.match(r'^[a-z0-9]+(-[a-z0-9]+)?$', name):
      import subprocess
      subprocess.run(['docker', 'stack', 'rm', name], check=True)

api = responder.API()

@api.route("/")
def index(req, res):
  res.html = api.template("index.html")

@api.route("/workspaces")
class WorkspaceCollectionResource:
  # GET /workspaces
  def on_get(self, req, res):
    res.media = {
      "workspaces": list(DockerHandler().list_workspaces())
    }

  # POST /workspaces
  # { workspace: 'playground1' }
  async def on_post(self, req, res):
    @api.background.task
    def process_adding_workspace(name):
       DockerHandler().add_workspace(name)

    json = await req.media()
    process_adding_workspace(json['workspace'])
    res.text = json['workspace']

@api.route("/workspaces/{workspace}")
class WorkspaceItemResource:
  # GET /workspaces/:workspace
  def on_get(self, req, res, *, workspace):
    res.media = {
      "workspace": DockerHandler().show_workspace(workspace)
    }

  # DELETE /workspaces/:workspace
  def on_delete(self, req, res, *, workspace):
    DockerHandler().remove_workspace(workspace)
    res.text = workspace


if __name__ == '__main__':
  api.run()
