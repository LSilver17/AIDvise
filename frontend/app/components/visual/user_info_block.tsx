import { Flex } from "@radix-ui/themes"

type PropTypes = {
    dataField: string,
    children: React.ReactNode,
}

export default function AccountField({dataField, children}: PropTypes) {
    return (
        <Flex direction="row">
            <Flex justify="start">
                {dataField}
            </Flex>
            <Flex justify="start">
                {children}
            </Flex>
        </Flex>
    );
}