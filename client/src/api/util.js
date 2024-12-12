export function isCachedResponseValid({
	cacheTime,
	intervalBeforeInvalidation = 1000 * 60 * 2,
	currentTime = new Date().getTime(),
}) {
	const cacheAge = currentTime - cacheTime;

	return cacheAge < intervalBeforeInvalidation;
}
