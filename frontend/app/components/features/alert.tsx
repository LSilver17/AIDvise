import { Flex, Text } from "@radix-ui/themes";
import { AlertStatus } from "@/app/lib/alert"
import AlertTitle from "@/app/components/visual/title"

type Props = {
    content: string;
    status: AlertStatus;
    courseOpening?: boolean;
    key: number;
}

export default function SingleAlert({content, status, courseOpening, key}: Props) {
    courseOpening = courseOpening ?? false;
    return (
        <Flex direction="column" width = "500px">
            <AlertTitle size="6">New Alert</AlertTitle>
            <Flex justify="between">
                <Text>{content}</Text>
                <Text>PHTime</Text>
            </Flex>
        </Flex>
    );
}