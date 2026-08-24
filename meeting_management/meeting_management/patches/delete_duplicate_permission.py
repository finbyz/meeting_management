import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count


def execute():
    CustomDocPerm = DocType("Custom DocPerm")

    duplicates = (
        frappe.qb.from_(CustomDocPerm)
        .select(
            CustomDocPerm.parent,
            CustomDocPerm.role,
            CustomDocPerm.permlevel,
            Count(CustomDocPerm.name).as_("count"),
        )
        .groupby(
            CustomDocPerm.parent,
            CustomDocPerm.role,
            CustomDocPerm.permlevel,
        )
        .having(Count(CustomDocPerm.name) > 1)
    ).run(as_dict=True)

    for duplicate in duplicates:
        records = frappe.get_all(
            "Custom DocPerm",
            filters={
                "parent": duplicate.parent,
                "role": duplicate.role,
                "permlevel": duplicate.permlevel,
            },
            fields=["name"],
            order_by="creation asc",
        )

        # Keep the first record, delete the rest
        for row in records[1:]:
            frappe.delete_doc(
                "Custom DocPerm",
                row.name,
                ignore_permissions=True,
                force=True,
            )

            frappe.logger().info(
                f"Deleted duplicate Custom DocPerm: {row.name} "
                f"(Doctype={duplicate.parent}, "
                f"Role={duplicate.role}, "
                f"PermLevel={duplicate.permlevel})"
            )

    frappe.db.commit()