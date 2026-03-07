import { ScrollArea, Text, Box, Flex } from "@radix-ui/themes";
import { AlertStatus, Alert } from "@/app/utils/alert"
import { alerts } from "@/mock/mock.json";


const userAlerts: Alert[] = [];

if (alerts.length != 0) {
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