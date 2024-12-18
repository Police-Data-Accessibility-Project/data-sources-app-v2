import { FOOTER_LINK_ICONS } from 'pdap-design-system';

export const ALL_LOCATION_TYPES = ['locality', 'county', 'state', 'federal'];

export const NAV_LINKS = [
	{
		path: '/',
		text: 'Search',
		method: 'route',
	},
	{
		href: 'https://pdap.io/data',
		text: 'Data',
		method: 'href',
	},
	{
		href: 'https://pdap.io/community',
		text: 'Community',
		method: 'href',
	},
	{
		href: 'https://pdap.io/about',
		text: 'About',
		method: 'href',
	},
	{
		href: 'https://pdap.io/donate',
		text: 'Donate',
		method: 'href',
	},
	{
		href: 'https://docs.pdap.io/',
		text: 'Docs',
		method: 'href',
	},
];

export const FOOTER_LINKS = [
	{
		href: 'https://github.com/orgs/Police-Data-Accessibility-Project',
		text: 'Github',
		icon: FOOTER_LINK_ICONS.GITHUB,
	},
	{
		href: 'https://discord.gg/wMqex8nKZJ',
		text: 'Discord',
		icon: FOOTER_LINK_ICONS.DISCORD,
	},
	{
		href: 'https://www.linkedin.com/company/pdap',
		text: 'LinkedIn',
		icon: FOOTER_LINK_ICONS.LINKEDIN,
	},
	{
		href: 'https://pdap.io/jobs',
		text: 'Jobs',
		icon: FOOTER_LINK_ICONS.JOBS,
	},
	{
		href: 'https://newsletter.pdap.io/',
		text: 'Newsletter',
		icon: FOOTER_LINK_ICONS.NEWSLETTER,
	},
	{
		href: 'https://docs.pdap.io/',
		text: 'Docs',
		icon: FOOTER_LINK_ICONS.DOCS,
	},
];

export const STATES_TO_ABBREVIATIONS = new Map([
	['Alabama', 'AL'],
	['Alaska', 'AK'],
	['American Samoa', 'AS'],
	['Arizona', 'AZ'],
	['Arkansas', 'AR'],
	['Armed Forces Americas', 'AA'],
	['Armed Forces Europe', 'AE'],
	['Armed Forces Pacific', 'AP'],
	['California', 'CA'],
	['Colorado', 'CO'],
	['Connecticut', 'CT'],
	['Delaware', 'DE'],
	['District Of Columbia', 'DC'],
	['Florida', 'FL'],
	['Georgia', 'GA'],
	['Guam', 'GU'],
	['Hawaii', 'HI'],
	['Idaho', 'ID'],
	['Illinois', 'IL'],
	['Indiana', 'IN'],
	['Iowa', 'IA'],
	['Kansas', 'KS'],
	['Kentucky', 'KY'],
	['Louisiana', 'LA'],
	['Maine', 'ME'],
	['Marshall Islands', 'MH'],
	['Maryland', 'MD'],
	['Massachusetts', 'MA'],
	['Michigan', 'MI'],
	['Minnesota', 'MN'],
	['Mississippi', 'MS'],
	['Missouri', 'MO'],
	['Montana', 'MT'],
	['Nebraska', 'NE'],
	['Nevada', 'NV'],
	['New Hampshire', 'NH'],
	['New Jersey', 'NJ'],
	['New Mexico', 'NM'],
	['New York', 'NY'],
	['North Carolina', 'NC'],
	['North Dakota', 'ND'],
	['Northern Mariana Islands', 'NP'],
	['Ohio', 'OH'],
	['Oklahoma', 'OK'],
	['Oregon', 'OR'],
	['Pennsylvania', 'PA'],
	['Puerto Rico', 'PR'],
	['Rhode Island', 'RI'],
	['South Carolina', 'SC'],
	['South Dakota', 'SD'],
	['Tennessee', 'TN'],
	['Texas', 'TX'],
	['US Virgin Islands', 'VI'],
	['Utah', 'UT'],
	['Vermont', 'VT'],
	['Virginia', 'VA'],
	['Washington', 'WA'],
	['West Virginia', 'WV'],
	['Wisconsin', 'WI'],
	['Wyoming', 'WY'],
]);
