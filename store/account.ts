import { defineStore } from "pinia";

interface matchListReturn {
	url: string;
	matches: any[];
	start: string;
}

export default defineStore("account", () => {
	const name = ref<string>("");
	const tag = ref<string>("");

	const profile = ref<any>(null);

	const matchList = ref<matchListReturn>({
		url: "",
		matches: [],
		start: "",
	});

	const setAccount = async (account: { name: string; tag: string }) => {
		name.value = account.name;
		tag.value = account.tag;

		const riot_id = await $fetch("/api/account", {
			params: {
				name: name.value,
				tag: tag.value,
			},
		});

		profile.value = riot_id;
	};

	const getMatches = async (page: number = 1) => {
		if (!profile.value) {
			throw new Error("Profile not set. Please set the account first.");
		}

		const matches = await $fetch("/api/account/matches", {
			params: {
				name: name.value,
				tag: tag.value,
				page: page,
			},
		});
		return matches;
	};

	const getMatchesByTime = async (start: string, end: string, url: string) => {
		const matches: any = await $fetch("/api/account/matches/time", {
			params: {
				name: name.value,
				tag: tag.value,
				start: start,
				end: end,
				url: url,
			},
		});
		matchList.value = matches[0];
	};

	const setMatchList = (matches: any) => {
		matchList.value = matches;
	};

	return {
		name,
		tag,
		matchList,
		profile,
		setAccount,
		getMatches,
		setMatchList,
		getMatchesByTime,
	};
});
