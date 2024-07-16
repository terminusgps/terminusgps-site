function updateAssetName(event) {
	const firstName = document.getElementById("id_first_name");
	const assetName = document.getElementById("id_asset_name");
	const baseEnding = "'s Ride";

	if (event.isTrusted) {
		assetName.value = firstName.value + baseEnding;
	}
}

document.addEventListener("DOMContentLoaded", function () {
	const firstName = document.getElementById("id_first_name");
	const assetName = document.getElementById("id_asset_name");

	firstName.addEventListener("input", updateAssetName);
	assetName.addEventListener("input", function (event) {
		if (event.isTrusted) {
			firstName.removeEventListener("input", updateAssetName);
		}
	});
});
