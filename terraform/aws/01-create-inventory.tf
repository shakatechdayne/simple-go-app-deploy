
# Variables
variable "inventoryDir" {}

resource "null_resource" "ansible-provision" {
  depends_on = ["aws_security_group.webSg", "aws_security_group.appSg", "aws_security_group.buildSg", "aws_instance.appIns", "aws_instance.webIns", "aws_instance.buildIns"]

  # Create Web Node Inventory
  provisioner "local-exec" {
    command = "echo '[webnode]\n${aws_instance.webIns.public_ip} ansible_private_key_file=${var.inventoryDir}/${var.keyPair}.pem' > ${var.inventoryDir}/inventory.ini"
  }

  # Create Build Node Inventory
  provisioner "local-exec" {
    command = "echo '\n[buildnode]\n${aws_instance.buildIns.public_ip} ansible_private_key_file=${var.inventoryDir}/${var.keyPair}.pem' >> ${var.inventoryDir}/inventory.ini"
  }

  # Create App Nodes Inventory
  provisioner "local-exec" {
    command = "echo '\n[appnode]' >> ${var.inventoryDir}/inventory.ini"
  }

  provisioner "local-exec" {
    command = "echo '${join("\n",formatlist("%s ansible_private_key_file=%s", aws_instance.appIns.*.public_ip, concat(var.inventoryDir,"/",var.keyPair,".pem")))}' >> ${var.inventoryDir}/inventory.ini"
  }
}
