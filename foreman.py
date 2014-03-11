from base64 import b64encode
import json
import urllib2
from sys import stderr, exit

class Foreman:
  def __init__(self,profile):
    self.url = profile['url']
    self.user = profile['user']
    self.auth = b64encode('%s:%s' % (profile['user'],profile['pw']))
    self.pw = profile['pw']

  def get_api(self,api,method=None,data=None):
    """"
    Helper function for calling Foreman. Requires a url, endpoint, http method
    (if other than GET), and authorization. Returns a json object.
    """

    endpoint = "%s%s" % (self.url,api)

    # Generate a request acceptable to the foreman API
    request = None

    request = urllib2.Request(endpoint)
    request.add_header("Authorization", "Basic %s" % self.auth)
    request.add_header('Content-Type', 'application/json')

    # Data payloads require you to specify a method, either put or post
    if data:
      try:
        request.get_method = lambda: method
        return json.load(urllib2.urlopen(request,data))
      except urllib2.HTTPError as e:
        stderr.write("Unable to fulfill request: %s" % e)
    else:
      try:
        return json.load(urllib2.urlopen(request))
      except urllib2.HTTPError as e:
        stderr.write("Unable to fulfill request: %s" % e)

  def describe_instances(self,filter=None):
    """
    Prints all the instancess within a group. Can filter by a comma separated
    list of hosts.
    """
    results = {}
    hosts = self.get_api("/hosts")
    for i in hosts:
      name = i['host']['name']
      results[name] = {}
      for k, v in i['host'].iteritems():
        results[name][k] = v

    if filter:
      filter_hosts = {}
      for i in filter.split(','):
        try:
          filter_hosts[i] = results[i]
        except KeyError:
          filter_hosts[i] = "Not found"
      return filter_hosts
    else:
      return results

  def describe_groups(self,filter=None,pretty=False):
    """
    List the groups and their relevant IDs. Can filter by name.
    """
    results = {}
    groups = self.get_api("/hostgroups")
    for i in groups:
      name = i['hostgroup']['name']
      results[name] = {}
      for k, v in i['hostgroup'].iteritems():
        results[name][k] = v

    if filter:
      filter_groups = {}
      for group in filter.split(','):
        try:
          filter_groups[group] = results[group]
        except KeyError:
          filter_groups[group] = "Not found"
      results = filter_groups
    return results

  def describe_tenants(self,filter=None):
    "A helper function that displays hosts that match a group name"
    filtered_results = {}
    hosts = self.describe_instances()
    groups = self.describe_groups()

    filter = [int(f) for f in filter.split(',')]
    print filter
    for host in hosts.values():
      if host['hostgroup_id'] in filter:
        filtered_results[host['name']] = host
    return filtered_results
