// Copyright (c) 2026, Shivangi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("SNM Task", {
//     refresh(frm) {

//     },
// });
frappe.ui.form.on("SNM Task",{
    refresh:function(frm){
        if(frm.doc.__islocal){

            frm.call({
                method:"get_task_no",
                doc:frm.doc
            })
        }
        if (frm.doc.is_group){

             frm.add_custom_button(__("Create Sub Task"), function () {

            frappe.route_options = {
                parent_task: frm.doc.name,
                subject: frm.doc.subject
            };

            frappe.set_route("Form", "SNM Task", "new-task");

        }).css({
                "background-color": "black",
                "color": "#fff",
                "border-radius": "8px",
                "font-weight": "600",
                "padding": "6px 14px"
            });
        }
        get_dept(frm)
        },
    parent_task(frm){
        frm.call({
            method:"get_task_no",
            doc:frm.doc
        })

    },
    allocated_by(frm){
        get_dept(frm)
    }
})

function get_dept(frm){
    frm.call({
        method:"get_dept",
        doc:frm.doc
    })
}