import { ScrollArea, Text, Box, Flex } from "@radix-ui/themes";
import { AlertStatus, Alert } from "@/app/lib/alert"
import { alerts } from "@/mock/mock.json";
// TODO: import from DB

// final alerts list
const userAlerts: Alert[] = [];

// TODO: populate list with DB alerts instead of JSON alerts
if (alerts.length != 0) {
    // iterates through alert list from JSON, storing in new list
    alerts.forEach(curr => {
        var status = ((stat: string) => 
            stat == "Unseen" ? 0 : 1)
        (curr.status);
        var alert = new Alert(curr.message, status);
        userAlerts.push(alert);
    })
}

export default function Alerts () {
    return (
        <ScrollArea type="scroll" style = {{width: "100%", height: "100%", minHeight: "0"}}>
            <Box className="nightBG">
                <ul>
                    {
                        userAlerts.map((alert, i) => (
                            <li key={i}>{alert.getStatus()}: {alert.getMessage()}</li>
                        ))
                    }
                </ul>
            </Box>
        </ScrollArea>
    );
}