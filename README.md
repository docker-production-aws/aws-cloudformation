# AWS CloudFormation Role

This is an Ansible role for generating CloudFormation templates and deploying CloudFormation stacks to Amazon Web Services.

## Requirements

- Python 2.7
- PIP package manager (**easy_install pip**)
- Ansible 2.4 or greater (**pip install ansible**)
- Boto3 (**pip install boto3**)
- Netaddr (**pip install netaddr**)
- AWS CLI (**pip install awscli**) installed and configured

## Setup

The recommended approach to use this role is an Ansible Galaxy requirement to your Ansible playbook project.

The role should be placed in the folder **roles/aws-cloudformation**, and can then be referenced from your playbooks as a role called `aws-cloudformation`.

You should also specify a specific release that is compatible with your playbook.

### Installation using Ansible Galaxy

To set this role up as an Ansible Galaxy requirement, first create a `requirements.yml` file in a `roles` subfolder of your playbook and add an entry for this role.  See the [Ansible Galaxy documentation](http://docs.ansible.com/ansible/galaxy.html#installing-multiple-roles-from-a-file) for more details.

```
# Example requirements.yml file
- src: https://github.com/docker-in-production/aws-cloudformation.git
  scm: git
  version: v1.0
  name: aws-cloudformation
```

Once you have created `requirements.yml`, you can install the role using the `ansible-galaxy` command line tool.

```
$ ansible-galaxy install -r roles/requirements.yml -p ./roles/ --force
```

To update the role version, simply update the `requirements.yml` file and re-install the role as demonstrated above.

## Usage

This role is designed to be used with CloudFormation stacks and relies on a CloudFormation template file being provided by the consuming playbook.

The default convention is to create the template file at the path `templates/stack.yml.j2` in the playbook repository.  

> You can override the default template file by setting the `Stack.Template` variable.

The expected format of the CloudFormation template is a [Jinja2 template](http://jinja.pocoo.org/docs/dev/), although you can provide a literal template.  This allows you to perform Jinja2 template variable substitution and more advanced constructs to generate your CloudFormation templates. 

The recommended approach is to describe your template in a YAML format, as this role will automatically convert to a minified JSON format.

> This role does not currently support AWS YAML syntax.  The role will convert your template and upload the template as minified JSON.

The following variables are used to configure this role:

- `Stack.Name` (required) - defines the stack name
- `Stack.Inputs` (optional) - a dictionary of stack inputs to provide to the stack.  This is required if your stack has any mandatory input parameters.
- `Stack.Policy` (optional) - defines the stack policy in a YAML or JSON format.
- `Stack.Bucket` (optional) - defines the S3 bucket where the CloudFormation template will be uploaded.  This defaults to `<account-id>-cfn-templates` if not specified.
- `Stack.Upload` (optional) - uploads the generated CloudFormation template to an S3 bucket defined by the `Stack.Bucket` variable.  Defaults to `false`.

Invoking this role will generate a folder called `build` in the current working directory, along with a timestamped folder of the current date (e.g. `./build/20160705154440/`).  Inside this folder the following files are created:

- `stack.yml` - the generated CloudFormation template in human readable YAML format.
- `stack.json` - the generated CloudFormation template in compact JSON format.  This is the template that is uploaded to the AWS CloudFormation service when creating or updating a stack.
- `policy.json` - the stack policy JSON file that is uploaded to the AWS CloudFormation service.

### S3 Template Upload

The S3 template upload feature is disabled by default, but can be enabled if required by setting the variable `Stack.Upload` to `true`.

The `stack.json` template will be uploaded to an S3 bucket as defined by the variable `Stack.Bucket`.

### Generating a Template Only

You can generate a template only by passing the tag `generate` to this role.  This will only create the templates as described above, but not attempt to create or update the stack in CloudFormation.

`ansible-playbook site.yml -e env=dev --tags generate`

Note the generated template will be uploaded to S3 as described earlier.

### Temporarily Disabling Stack Policy

You can temporarily disable the stack policy for a provisioning run by setting the variable `Stack.DisablePolicy` to true:

`ansible-playbook site.yml -e env=prod -e Stack.DisablePolicy=true`

This will set to the stack policy to the following policy before stack modification:

```
{
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : "Update:*",
        "Principal": "*",
        "Resource" : "*"
      }
    ]
  }
```

And then after stack modification is complete, reset the stack policy to it's previous state.  

> Note: This role will also reset the stack policy in the event of a stack modification failure

### Role Facts

This role sets the following facts that you can use subsequently in your roles:

- `cloudformation['<stack-name>']` - CloudFormation facts about the created stack.  This includes stack resources and stack outputs.
- `Stack.Facts` - CloudFormation facts about the created stack.  This includes stack resources and stack outputs and is identical to the `cloudformation['<stack-name>']` fact.
- `Stack.Url` - S3 URL of the CloudFormation template.

## Examples

### Invoking the Role

The following is an example of a playbook configured to use this role.  Note the use of the [AWS STS role](https://github.com/docker-production-aws/aws-sts.git) to obtain STS credentials is separate from this role.

```
---
- name: STS Assume Role Playbook
  hosts: "{{ env }}"
  gather_facts: no
  environment:
  vars:
    Sts:
      Role: "arn:aws:iam::123456789:role/admin"
      SessionName: testAssumeRole
      Region: us-west-2
  roles:
  - aws_sts

- name: Stack Deployment Playbook
  hosts: "{{ env }}"
  environment: "{{ Sts.Credentials }}"
  roles:
    - aws-cloudformation
```

## Release Notes

### Version 1.0

- First Release
