output "appNode1ip" {
  value = "${element(aws_instance.appIns.*.private_ip, 0)}"
}

output "appNode2ip" {
  value = "${element(aws_instance.appIns.*.private_ip, 1)}"
}

output "webNodeIp" {
  value = "${aws_instance.webIns.public_ip}"
}

output "buildNodeIp" {
  value = "${aws_instance.buildIns.public_ip}"
}
