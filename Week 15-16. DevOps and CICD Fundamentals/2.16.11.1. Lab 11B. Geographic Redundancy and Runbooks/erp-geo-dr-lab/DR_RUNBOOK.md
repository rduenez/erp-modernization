# ERP Disaster Recovery Runbook (Tier 1 Outage)

**Trigger:** Total loss of primary region (`us-east-1`).
**Target RPO:** 15 minutes.
**Target RTO:** 1 hour.

## Phase 1: Assess and Declare (Minutes 0-10)
- [ ] Confirm outage via AWS Service Health Dashboard.
- [ ] VP of Engineering officially declares "Disaster Status".
- [ ] Notify stakeholders via PagerDuty/Slack #incident-management.

## Phase 2: Infrastructure Restoration (Minutes 10-30)
- [ ] Check out the latest stable production release tag from Git: `git checkout tags/v2.4.1`
- [ ] Initialize Terraform with the DR state file: `terraform workspace select dr-oregon`
- [ ] Execute `terraform apply -var-file="dr.tfvars"` to provision Kubernetes/Fargate clusters in `us-west-2`.

## Phase 3: Data Restoration (Minutes 30-50)
- [ ] Identify the latest replicated automated snapshot in `us-west-2` RDS.
- [ ] Restore the database using Point-In-Time Recovery (PITR) to the exact minute before the outage.
- [ ] Secrets Manager replica is automatically available in `us-west-2`. No manual sync required.

## Phase 4: DNS Cutover and Verification (Minutes 50-60)
- [ ] Update Route53 DNS to point `erp.company.com` to the new `us-west-2` Load Balancer.
- [ ] QA team executes Smoke Tests against the new endpoints.
- [ ] Notify stakeholders: "System Restored. Operating out of DR Region."
