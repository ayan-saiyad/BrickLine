import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "20s", target: 5 },
    { duration: "60s", target: 10 },
    { duration: "20s", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.02"],
    http_req_duration: ["p(95)<500"],
  },
};

const baseUrl = __ENV.BASE_URL || "http://127.0.0.1:18080";

export default function () {
  const response = http.get(`${baseUrl}/api/sets?page_size=24`);
  check(response, { "sets endpoint is healthy": (result) => result.status === 200 });
  sleep(0.5);
}

