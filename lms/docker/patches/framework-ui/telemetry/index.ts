export function useTelemetry() {
	return {
		capture: (event?: string, data?: any) => {},
	}
}
export const telemetryPlugin = {
	install(app?: any, options?: any) {},
}
