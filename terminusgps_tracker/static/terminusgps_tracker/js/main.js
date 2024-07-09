function updateAssetName(event) {
	console.log("Running updateAssetName. Event isTrusted: ", event.isTrusted);
	const firstName = document.getElementById("first_name");
	const assetName = document.getElementById("asset_name");
	const baseEnding = "'s Ride";

	if (event.isTrusted) {
		assetName.value = firstName.value + baseEnding;
	}
}

document.addEventListener("DOMContentLoaded", function () {
	const firstName = document.getElementById("first_name");
	const assetName = document.getElementById("asset_name");

	firstName.addEventListener("input", updateAssetName);
	assetName.addEventListener("input", function (event) {
		if (event.isTrusted) {
			firstName.removeEventListener("input", updateAssetName);
		}
	});
});
