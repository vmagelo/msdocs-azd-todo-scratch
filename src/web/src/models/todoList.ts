import { TodoItem } from "./todoItem";

export interface TodoList {
    id?: number
    name: string
    items?: TodoItem[]
    description?: string
    createdDate?: Date
    updatedDate?: Date
}