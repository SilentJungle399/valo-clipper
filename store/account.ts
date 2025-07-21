import { defineStore } from "pinia";

export default defineStore("account", () => {
	const name = ref<string>("");
	const tag = ref<string>("");

	const profile = ref<any>(null);

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

	return {
		name,
		tag,
		profile,
		setAccount,
		getMatches,
	};
});
