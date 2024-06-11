const state = {
	autoUpdateEnabled: true,
};

function getAutoUpdateEnabled() {
	return state.autoUpdateEnabled;
}

function setAutoUpdateEnabled(value) {
	state.autoUpdateEnabled = value;
}

function updateAssetName() {
	const assetName = document.getElementById("id_asset_name");
	const firstName = document.getElementById("id_first_name");
	const defaultEnding = "'s Ride";

	if (getAutoUpdateEnabled()) {
		assetName.value = firstName.value + defaultEnding;
	}
}

function disableAutoUpdate(event) {
	if (event.isTrusted) {
		setAutoUpdateEnabled(false);
	}
}

document
	.getElementById("id_first_name")
	.addEventListener("input", updateAssetName);

document
	.getElementById("id_asset_name")
	.addEventListener("input", disableAutoUpdate);
