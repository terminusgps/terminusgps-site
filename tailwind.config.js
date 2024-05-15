/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		"./ecom/templates/*.html",
		"./ecom/templates/**/*.html",
		"./blog/templates/*.html",
		"./blog/templates/**/*.html",
		"./dforms/templates/*.html",
		"./dforms/templates/**/*.html",
	],
	theme: {
		extend: {
			colors: {
				"terminus-black": "#0B090A",
				"terminus-gray": "#161A1D",
				"terminus-darker-red": "#660708",
				"terminus-dark-red": "#A4161A",
				"terminus-red": "#BA181B",
				"terminus-light-red": "#E5383B",
				"terminus-light-gray": "#B1A7A6",
				"terminus-lighter-gray": "#D3D3D3",
				"terminus-off-white": "#F5F3F4",
			},
			backgroundImage: {
				"hero-pattern": "url('/static/images/cars.webp')",
				"moto-hero-pattern": "url('/static/images/moto.webp')",
				"convertible-hero-pattern": "url('/static/images/convertible.jpg')",
			},
			animation: {
				wiggle: "wiggle 1s ease-in-out infinite",
			},
		},
	},
	plugins: [],
};
