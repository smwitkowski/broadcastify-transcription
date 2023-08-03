# Variables
PROJECT_ID=personal-project-space-353201
CLUSTER_NAME=general-project-autocluster
NAMESPACE=default
GSA_NAME=label-studio-gsa
KSA_NAME=label-studio-ksa
LOCATION=us-central1

# Enable Workload Identity on your cluster
enable-workload-identity:
	gcloud container clusters update $(CLUSTER_NAME) --workload-pool=$(PROJECT_ID).svc.id.goog --location $(LOCATION)

# Create the GSA
create-gsa:
	gcloud iam service-accounts create $(GSA_NAME)
	gcloud projects add-iam-policy-binding $(PROJECT_ID) --member="serviceAccount:$(GSA_NAME)@$(PROJECT_ID).iam.gserviceaccount.com" --role="roles/storage.objectAdmin"

# Create the KSA
create-ksa:
	kubectl create serviceaccount $(KSA_NAME) --namespace $(NAMESPACE)

# Link the GSA with the KSA
link-accounts:
	gcloud iam service-accounts add-iam-policy-binding \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$(PROJECT_ID).svc.id.goog[$(NAMESPACE)/$(KSA_NAME)]" \
    $(GSA_NAME)@$(PROJECT_ID).iam.gserviceaccount.com

# Target to set up service accounts
setup-service-accounts: create-gsa create-ksa link-accounts
